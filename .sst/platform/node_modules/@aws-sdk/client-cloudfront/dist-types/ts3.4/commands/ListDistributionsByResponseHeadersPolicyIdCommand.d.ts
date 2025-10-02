import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  ListDistributionsByResponseHeadersPolicyIdRequest,
  ListDistributionsByResponseHeadersPolicyIdResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListDistributionsByResponseHeadersPolicyIdCommandInput
  extends ListDistributionsByResponseHeadersPolicyIdRequest {}
export interface ListDistributionsByResponseHeadersPolicyIdCommandOutput
  extends ListDistributionsByResponseHeadersPolicyIdResult,
    __MetadataBearer {}
export declare class ListDistributionsByResponseHeadersPolicyIdCommand extends $Command<
  ListDistributionsByResponseHeadersPolicyIdCommandInput,
  ListDistributionsByResponseHeadersPolicyIdCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListDistributionsByResponseHeadersPolicyIdCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListDistributionsByResponseHeadersPolicyIdCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListDistributionsByResponseHeadersPolicyIdCommandInput,
    ListDistributionsByResponseHeadersPolicyIdCommandOutput
  >;
  private serialize;
  private deserialize;
}
