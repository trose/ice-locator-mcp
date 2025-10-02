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
  ListDistributionsByOriginRequestPolicyIdRequest,
  ListDistributionsByOriginRequestPolicyIdResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListDistributionsByOriginRequestPolicyIdCommandInput
  extends ListDistributionsByOriginRequestPolicyIdRequest {}
export interface ListDistributionsByOriginRequestPolicyIdCommandOutput
  extends ListDistributionsByOriginRequestPolicyIdResult,
    __MetadataBearer {}
export declare class ListDistributionsByOriginRequestPolicyIdCommand extends $Command<
  ListDistributionsByOriginRequestPolicyIdCommandInput,
  ListDistributionsByOriginRequestPolicyIdCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListDistributionsByOriginRequestPolicyIdCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListDistributionsByOriginRequestPolicyIdCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListDistributionsByOriginRequestPolicyIdCommandInput,
    ListDistributionsByOriginRequestPolicyIdCommandOutput
  >;
  private serialize;
  private deserialize;
}
