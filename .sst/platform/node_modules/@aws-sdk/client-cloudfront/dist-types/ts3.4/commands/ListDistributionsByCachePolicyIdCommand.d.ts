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
  ListDistributionsByCachePolicyIdRequest,
  ListDistributionsByCachePolicyIdResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListDistributionsByCachePolicyIdCommandInput
  extends ListDistributionsByCachePolicyIdRequest {}
export interface ListDistributionsByCachePolicyIdCommandOutput
  extends ListDistributionsByCachePolicyIdResult,
    __MetadataBearer {}
export declare class ListDistributionsByCachePolicyIdCommand extends $Command<
  ListDistributionsByCachePolicyIdCommandInput,
  ListDistributionsByCachePolicyIdCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListDistributionsByCachePolicyIdCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListDistributionsByCachePolicyIdCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListDistributionsByCachePolicyIdCommandInput,
    ListDistributionsByCachePolicyIdCommandOutput
  >;
  private serialize;
  private deserialize;
}
